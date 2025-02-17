<!--
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

<template>
  <dropdown-panel
    :text="(isCustom && CUSTOM_TITLE) || selectedRange.title"
    :inline="inline"
    :close-on-click="false"
  >
    <template #default="{ closePanel }">
      <div class="date-range-picker-panel">
        <div class="date-range-picker-body">
          <div class="date-range-picker-preset">
            <div style="border-right: 1px solid gray;">
              <header>Quick Ranges</header>
              <div class="preset-list">
                <div v-for="(rangeSet, index) in RANGE_SETS" :key="index" class="preset-column">
                  <div
                    v-for="range in rangeSet"
                    :key="range.title"
                    class="preset-value"
                    :class="{ selected: range === selectedRange }"
                  >
                    <hue-link @click="quickSelect(range, closePanel)">
                      {{ range.title }}
                    </hue-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="date-range-picker-custom">
            <header>Time Range</header>
            <div>
              <div class="range-header">FROM:</div>
              <datepicker
                v-model="customFrom"
                :typeable="true"
                input-class="range-input"
                calendar-class="range-calendar"
                format="dd/MM/yyyy"
                placeholder="DD/MM/YYYY"
              />
            </div>
            <div>
              <div class="range-header">TO:</div>
              <datepicker
                v-model="customTo"
                :typeable="true"
                input-class="range-input"
                calendar-class="range-calendar"
                format="dd/MM/yyyy"
                placeholder="DD/MM/YYYY"
              />
            </div>
          </div>
        </div>
        <div class="date-range-picker-footer">
          <hue-link @click="closePanel">Cancel</hue-link>
          <hue-button :primary="true" :small="true" @click="apply(closePanel)">Apply</hue-button>
        </div>
      </div>
    </template>
  </dropdown-panel>
</template>

<script lang="ts">
  import { defineComponent, ref, watch } from 'vue';

  import { Range } from './DateRangePicker';
  import { DateTime } from 'luxon';
  import Datepicker from 'vue3-datepicker';
  import HueLink from './HueLink.vue';
  import HueButton from './HueButton.vue';
  import I18n from '../utils/i18n';
  import DropdownPanel from './dropdown/DropdownPanel.vue';

  const SECOND = 1000;
  const MINUTE = 60 * SECOND;
  const HOUR = 60 * MINUTE;
  const DAY = 24 * HOUR;
  const WEEK = 7 * DAY;
  const MONTH = (365 / 12) * DAY;
  const YEAR = 365 * DAY;

  const RANGE_NOW = DateTime.utc();
  const TODAY_START = RANGE_NOW.valueOf() - RANGE_NOW.startOf('day').valueOf();
  const WEEK_START = RANGE_NOW.valueOf() - RANGE_NOW.startOf('week').valueOf();
  const MONTH_START = RANGE_NOW.valueOf() - RANGE_NOW.startOf('month').valueOf();
  const YEAR_START = RANGE_NOW.valueOf() - RANGE_NOW.startOf('year').valueOf();

  // Non-custom ranges have relative from/to, custom are absolute
  // due to third-party datepicker component.
  const RANGE_SETS: Range[][] = [
    [
      { title: I18n('Last 7 days'), from: 7 * DAY, to: 0 },
      { title: I18n('Last 30 days'), from: 30 * DAY, to: 0 },
      { title: I18n('Last 60 days'), from: 60 * DAY, to: 0 },
      { title: I18n('Last 90 days'), from: 90 * DAY, to: 0 },
      { title: I18n('Last 6 months'), from: 6 * MONTH, to: 0 },
      { title: I18n('Last 1 year'), from: YEAR, to: 0 },
      { title: I18n('Last 2 years'), from: 2 * YEAR, to: 0 },
      { title: I18n('Last 5 years'), from: 5 * YEAR, to: 0 }
    ],
    [
      { title: I18n('Last 5 minutes'), from: 5 * MINUTE, to: 0 },
      { title: I18n('Last 15 minutes'), from: 15 * MINUTE, to: 0 },
      { title: I18n('Last 30 minutes'), from: 30 * MINUTE, to: 0 },
      { title: I18n('Last 1 hour'), from: HOUR, to: 0 },
      { title: I18n('Last 3 hours'), from: 3 * HOUR, to: 0 },
      { title: I18n('Last 6 hours'), from: 6 * HOUR, to: 0 },
      { title: I18n('Last 12 hours'), from: 12 * HOUR, to: 0 },
      { title: I18n('Last 24 hours'), from: DAY, to: 0 }
    ],
    [
      { title: I18n('Today'), from: TODAY_START, to: 0 },
      { title: I18n('Yesterday'), from: TODAY_START + DAY, to: TODAY_START - 1 },
      { title: I18n('This week'), from: WEEK_START, to: 0 },
      { title: I18n('Last week'), from: WEEK_START + WEEK, to: WEEK_START - 1 },
      { title: I18n('This month'), from: MONTH_START, to: 0 },
      { title: I18n('Last month'), from: MONTH_START + MONTH, to: MONTH_START - 1 },
      { title: I18n('This year'), from: YEAR_START, to: 0 },
      { title: I18n('Last year'), from: YEAR_START + YEAR, to: YEAR_START - 1 }
    ]
  ];

  const DEFAULT_RANGE = RANGE_SETS[0][0];

  const CUSTOM_TITLE = I18n('Custom Range');

  export default defineComponent({
    name: 'DateRangePicker',
    components: {
      Datepicker,
      DropdownPanel,
      HueButton,
      HueLink
    },
    props: {
      inline: {
        type: Boolean,
        required: false,
        default: false
      }
    },
    emits: ['date-range-changed'],
    setup(props, { emit }) {
      const selectedRange = ref<Range>(DEFAULT_RANGE);
      const isCustom = ref<boolean>(false);
      const customFrom = ref<Date>(new Date(RANGE_NOW.toMillis() - DEFAULT_RANGE.from));
      const customTo = ref<Date>(new Date(RANGE_NOW.toMillis()));

      watch(customFrom, () => {
        if (customFrom.value.getTime() > customTo.value.getTime()) {
          customTo.value = customFrom.value;
        }
      });

      watch(customTo, () => {
        if (customTo.value.getTime() < customFrom.value.getTime()) {
          customFrom.value = customTo.value;
        }
      });

      const notify = (): void => {
        let range: Range;
        if (isCustom.value) {
          range = {
            title: CUSTOM_TITLE,
            from: DateTime.fromJSDate(customFrom.value).startOf('day').valueOf(),
            to: DateTime.fromJSDate(customTo.value).endOf('day').valueOf(),
            custom: true
          };
        } else {
          const { title, from, to } = selectedRange.value;
          const now = DateTime.utc().valueOf();
          range = {
            title,
            from: now - from,
            to: now - to
          };
        }
        emit('date-range-changed', range);
      };

      const clear = (): void => {
        if (isCustom.value || selectedRange.value !== DEFAULT_RANGE) {
          customFrom.value = new Date(RANGE_NOW.toMillis() - DEFAULT_RANGE.from);
          customTo.value = new Date(RANGE_NOW.toMillis());
          selectedRange.value = DEFAULT_RANGE;
          isCustom.value = false;
          notify();
        }
      };

      const apply = (closePanel: () => void): void => {
        isCustom.value = true;
        notify();
        closePanel();
      };

      const quickSelect = (range: Range, closePanel: () => void): void => {
        isCustom.value = false;
        selectedRange.value = range;
        notify();
        closePanel();
      };

      return {
        apply,
        clear,
        CUSTOM_TITLE,
        customFrom,
        customTo,
        isCustom,
        quickSelect,
        RANGE_SETS,
        selectedRange
      };
    }
  });
</script>

<style lang="scss" scoped>
  @import 'styles/colors';
  @import 'styles/mixins';

  .date-range-picker-panel {
    height: 250px;
    width: 700px;

    .date-range-picker-body {
      display: flex;
      flex-direction: row;
      border-bottom: 1px solid $hue-border-color;

      .date-range-picker-preset,
      .date-range-picker-custom {
        header {
          font-weight: 500;
          margin-bottom: 15px;
        }
      }

      .date-range-picker-preset {
        flex: 0 0 340px;
        padding: 15px 20px;

        .preset-list {
          display: flex;
          flex-direction: row;

          .preset-column {
            flex: 0 0 33%;
            font-size: 13px;
            line-height: 16px;

            .preset-value {
              padding: 1px 2px;

              &.selected {
                background-color: $fluid-gray-100;
              }
            }
          }
        }
      }

      .date-range-picker-custom {
        flex: 0 0 240px;
        padding: 15px 20px;

        .range-header {
          color: $fluid-gray-500;
          margin-bottom: 5px;
          text-transform: uppercase;
        }

        ::v-deep(.range-input) {
          padding: 4px;
          height: 28px;
          line-height: 24px;
          width: 100%;
          font-size: 13px;
          border: 1px solid $fluid-gray-800;
          border-radius: 3px;
        }

        ::v-deep(.range-calendar) {
          width: 230px;

          .cell {
            line-height: 30px;
            height: 30px;
          }
        }
      }
    }

    .date-range-picker-footer {
      line-height: 24px;
      text-align: right;
      padding: 6px 10px;

      a {
        font-size: 12px;
      }
    }
  }
</style>
