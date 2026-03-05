// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'state_filter_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(SelectedStates)
final selectedStatesProvider = SelectedStatesProvider._();

final class SelectedStatesProvider
    extends $NotifierProvider<SelectedStates, Set<String>> {
  SelectedStatesProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'selectedStatesProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$selectedStatesHash();

  @$internal
  @override
  SelectedStates create() => SelectedStates();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Set<String> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Set<String>>(value),
    );
  }
}

String _$selectedStatesHash() => r'f53c44dd31f45172d20e4b677888069ecfed0af4';

abstract class _$SelectedStates extends $Notifier<Set<String>> {
  Set<String> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<Set<String>, Set<String>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<Set<String>, Set<String>>,
              Set<String>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

@ProviderFor(filteredLeads)
final filteredLeadsProvider = FilteredLeadsProvider._();

final class FilteredLeadsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Map<String, dynamic>>>,
          List<Map<String, dynamic>>,
          FutureOr<List<Map<String, dynamic>>>
        >
    with
        $FutureModifier<List<Map<String, dynamic>>>,
        $FutureProvider<List<Map<String, dynamic>>> {
  FilteredLeadsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'filteredLeadsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$filteredLeadsHash();

  @$internal
  @override
  $FutureProviderElement<List<Map<String, dynamic>>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Map<String, dynamic>>> create(Ref ref) {
    return filteredLeads(ref);
  }
}

String _$filteredLeadsHash() => r'8a58fcedefe4a7eae904145a78622eea846eb7e7';
