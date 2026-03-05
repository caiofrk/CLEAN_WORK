import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'lead_provider.g.dart';

class MarketLead {
  final String id;
  final String clientName;
  final String opportunityDesc;
  final double? budgetEstimate;
  final DateTime? deadline;
  final String status;
  final String? sourceUrl;

  MarketLead({
    required this.id,
    required this.clientName,
    required this.opportunityDesc,
    this.budgetEstimate,
    this.deadline,
    required this.status,
    this.sourceUrl,
  });

  factory MarketLead.fromMap(Map<String, dynamic> map) {
    return MarketLead(
      id: map['id'],
      clientName: map['client_name'] ?? 'Unknown',
      opportunityDesc: map['opportunity_desc'] ?? '',
      budgetEstimate: map['budget_estimate'] != null
          ? double.tryParse(map['budget_estimate'].toString())
          : null,
      deadline: map['deadline'] != null
          ? DateTime.tryParse(map['deadline'].toString())
          : null,
      status: map['status'] ?? 'open',
      sourceUrl: map['source_url'],
    );
  }
}

@riverpod
Stream<List<MarketLead>> activeLeads(Ref ref) {
  return Supabase.instance.client
      .from('market_leads')
      .stream(primaryKey: ['id'])
      .eq('status', 'open')
      .map((data) => data.map((json) => MarketLead.fromMap(json)).toList());
}
