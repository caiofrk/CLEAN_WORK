// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'lead_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(activeLeads)
final activeLeadsProvider = ActiveLeadsProvider._();

final class ActiveLeadsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<MarketLead>>,
          List<MarketLead>,
          Stream<List<MarketLead>>
        >
    with $FutureModifier<List<MarketLead>>, $StreamProvider<List<MarketLead>> {
  ActiveLeadsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'activeLeadsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$activeLeadsHash();

  @$internal
  @override
  $StreamProviderElement<List<MarketLead>> $createElement(
    $ProviderPointer pointer,
  ) => $StreamProviderElement(pointer);

  @override
  Stream<List<MarketLead>> create(Ref ref) {
    return activeLeads(ref);
  }
}

String _$activeLeadsHash() => r'5c2400628ecb8c0183ede7afb0dbffa74c4840f8';
