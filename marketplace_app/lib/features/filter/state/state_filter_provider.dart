import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

part 'state_filter_provider.g.dart';

@riverpod
class SelectedStates extends _$SelectedStates {
  @override
  Set<String> build() => {'RJ', 'SP'}; // Default states

  void toggleState(String uf) {
    if (state.contains(uf)) {
      state = state.where((s) => s != uf).toSet();
    } else {
      state = {...state, uf};
    }
  }
}

// UI: O Feed de Produção filtrado por UF
@riverpod
Future<List<Map<String, dynamic>>> filteredLeads(Ref ref) async {
  final selectedUfs = ref.watch(selectedStatesProvider);

  if (selectedUfs.isEmpty) return [];

  final response = await Supabase.instance.client
      .from('br_production_leads')
      .select()
      .inFilter('uf', selectedUfs.toList())
      .order('data_postagem', ascending: false);

  return List<Map<String, dynamic>>.from(response);
}
