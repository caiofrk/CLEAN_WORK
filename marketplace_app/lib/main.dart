import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:url_launcher/url_launcher.dart';
import 'features/filter/state/state_filter_provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");

  await Supabase.initialize(
    url: dotenv.env['SUPABASE_URL'] ?? '',
    anonKey: dotenv.env['SUPABASE_KEY'] ?? '',
  );

  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Audiovisual Call Sheet',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const CallSheetPage(title: 'Brasil Audiovisual'),
    );
  }
}

class CallSheetPage extends ConsumerWidget {
  const CallSheetPage({super.key, required this.title});
  final String title;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final filteredLeadsAsyncValue = ref.watch(filteredLeadsProvider);
    final selectedStates = ref.watch(selectedStatesProvider);
    final availableStates = ['RJ', 'SP', 'MG', 'RS', 'SC', 'PR', 'BA'];

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        backgroundColor: Colors.blueAccent,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Filter Row
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: availableStates.map((uf) {
                final isSelected = selectedStates.contains(uf);
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: FilterChip(
                    label: Text(uf),
                    selected: isSelected,
                    onSelected: (_) {
                      ref.read(selectedStatesProvider.notifier).toggleState(uf);
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const Divider(),
          // Feed
          Expanded(
            child: filteredLeadsAsyncValue.when(
              data: (leads) {
                if (leads.isEmpty) {
                  return const Center(
                    child: Text("Nenhuma chamada ativa no momento."),
                  );
                }
                return ListView.builder(
                  itemCount: leads.length,
                  itemBuilder: (context, index) {
                    final lead = leads[index];
                    final String projeto = lead['projeto_nome'] ?? 'Sem Título';
                    final String uf = lead['uf'] ?? '';
                    final String cidade =
                        lead['cidade'] ?? 'Local não especificado';
                    final List<dynamic> vagasRaw = lead['vagas'] ?? [];
                    final List<String> vagas = vagasRaw
                        .map((v) => v.toString())
                        .toList();
                    final String desc = lead['descricao_original'] ?? '';
                    final String contato = lead['contato_producao'] ?? '';
                    final String urlOrigem = lead['url_origem'] ?? '';

                    return Card(
                      margin: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      elevation: 3,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    projeto,
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleMedium
                                        ?.copyWith(fontWeight: FontWeight.bold),
                                  ),
                                ),
                                Chip(
                                  label: Text(uf),
                                  backgroundColor: Colors.deepPurple.shade100,
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text("📍 $cidade"),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 8,
                              children: vagas
                                  .map(
                                    (v) => Chip(
                                      label: Text(
                                        v,
                                        style: const TextStyle(fontSize: 12),
                                      ),
                                      padding: EdgeInsets.zero,
                                    ),
                                  )
                                  .toList(),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              desc,
                              style: Theme.of(context).textTheme.bodySmall,
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                if (urlOrigem.isNotEmpty) ...[
                                  TextButton.icon(
                                    onPressed: () async {
                                      final launchUri = Uri.parse(urlOrigem);
                                      if (await canLaunchUrl(launchUri)) {
                                        await launchUrl(
                                          launchUri,
                                          mode: LaunchMode.externalApplication,
                                        );
                                      }
                                    },
                                    icon: const Icon(Icons.link),
                                    label: const Text('Fonte'),
                                  ),
                                  const SizedBox(width: 8),
                                ],
                                ElevatedButton.icon(
                                  onPressed: () async {
                                    if (contato.isEmpty) {
                                      ScaffoldMessenger.of(
                                        context,
                                      ).showSnackBar(
                                        const SnackBar(
                                          content: Text(
                                            'Nenhum contato encontrado. Tente via mensagem direta.',
                                          ),
                                        ),
                                      );
                                      return;
                                    }

                                    Uri? launchUri;
                                    if (contato.contains('@') &&
                                        !contato.startsWith('@') &&
                                        contato.contains('.')) {
                                      launchUri = Uri(
                                        scheme: 'mailto',
                                        path: contato,
                                      );
                                    } else if (contato.startsWith('@')) {
                                      launchUri = Uri.parse(
                                        'https://instagram.com/${contato.substring(1)}',
                                      );
                                    } else if (contato.startsWith('http')) {
                                      launchUri = Uri.parse(contato);
                                    }

                                    if (launchUri != null &&
                                        await canLaunchUrl(launchUri)) {
                                      await launchUrl(
                                        launchUri,
                                        mode: LaunchMode.externalApplication,
                                      );
                                    } else {
                                      if (context.mounted) {
                                        ScaffoldMessenger.of(
                                          context,
                                        ).showSnackBar(
                                          SnackBar(
                                            content: Text('Contato: $contato'),
                                          ),
                                        );
                                      }
                                    }
                                  },
                                  icon: const Icon(Icons.send),
                                  label: const Text('Aplicar'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) =>
                  Center(child: Text("Erro ao carregar: $error")),
            ),
          ),
        ],
      ),
    );
  }
}
