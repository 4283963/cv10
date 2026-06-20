<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">送货指引</h2>
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="color: #606266; font-size: 14px;">配送日期：</span>
        <el-date-picker
          v-model="deliveryDate"
          type="date"
          value-format="YYYY-MM-DD"
          :clearable="false"
          style="width: 180px;"
          @change="loadData"
        />
        <el-switch
          v-model="includeUnpacked"
          active-text="含未打包"
          inactive-text="仅已打包"
          style="margin-left: 8px;"
          @change="loadData"
        />
        <el-button type="primary" :icon="Refresh" @click="loadData">刷新路线</el-button>
      </div>
    </div>

    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="8">
        <div class="stat-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <div class="stat-label" style="color: rgba(255,255,255,0.9);">送货点数</div>
          <div class="stat-value" style="color: #fff;">{{ routeData?.total_points || 0 }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
          <div class="stat-label" style="color: rgba(255,255,255,0.9);">总行驶里程(公里)</div>
          <div class="stat-value" style="color: #fff;">{{ routeData?.total_distance_km || 0 }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
          <div class="stat-label" style="color: #606266;">待送达订单总数</div>
          <div class="stat-value" style="color: #303133;">{{ totalOrderCount }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px;">
              <el-icon :size="18" color="#409eff"><MapLocation /></el-icon>
              <span style="font-weight: 600; font-size: 15px;">送货路线图</span>
            </div>
          </template>
          <div style="position: relative; background: #f8fafc; border-radius: 8px; padding: 20px; min-height: 560px;">
            <svg v-if="routeData && routeData.route.length > 0"
                 viewBox="0 0 420 560"
                 style="width: 100%; height: 560px;"
            >
              <defs>
                <marker id="arrow" markerWidth="10" markerHeight="7"
                        refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#409eff" />
                </marker>
              </defs>

              <circle :cx="warehousePos.x" :cy="warehousePos.y" r="26" fill="#ff6b6b" />
              <circle :cx="warehousePos.x" :cy="warehousePos.y" r="20" fill="#fff" />
              <text :x="warehousePos.x" :y="warehousePos.y - 34"
                    text-anchor="middle" font-size="12" fill="#606266" font-weight="600">
                仓库(起点)
              </text>
              <text :x="warehousePos.x" :y="warehousePos.y + 4"
                    text-anchor="middle" font-size="14" fill="#ff6b6b" font-weight="bold">
                仓
              </text>

              <template v-for="(p, i) in routeData.route" :key="p.pickup_point.id">
                <line
                  v-if="i === 0"
                  :x1="warehousePos.x"
                  :y1="warehousePos.y + 26"
                  :x2="getPointPos(i).x"
                  :y2="getPointPos(i).y - 24"
                  stroke="#409eff"
                  stroke-width="2.5"
                  stroke-dasharray="6,4"
                  marker-end="url(#arrow)"
                />
                <line
                  v-else
                  :x1="getPointPos(i - 1).x"
                  :y1="getPointPos(i - 1).y + 24"
                  :x2="getPointPos(i).x"
                  :y2="getPointPos(i).y - 24"
                  stroke="#409eff"
                  stroke-width="2.5"
                  stroke-dasharray="6,4"
                  marker-end="url(#arrow)"
                />

                <rect :x="getPointPos(i).x - 32" :y="getPointPos(i).y - 20"
                      width="64" height="40" rx="20"
                      :fill="p.status === 'loaded' ? '#67c23a' : p.status ? '#409eff' : '#e6a23c'" />
                <rect :x="getPointPos(i).x - 28" :y="getPointPos(i).y - 16"
                      width="56" height="32" rx="16" fill="#fff" />
                <text :x="getPointPos(i).x" :y="getPointPos(i).y + 5"
                      text-anchor="middle" font-size="15"
                      :fill="p.status === 'loaded' ? '#67c23a' : p.status ? '#409eff' : '#e6a23c'"
                      font-weight="bold">
                  {{ p.sequence }}
                </text>
                <text :x="getPointPos(i).x" :y="getPointPos(i).y - 30"
                      text-anchor="middle" font-size="11" fill="#303133" font-weight="500">
                  {{ truncateText(p.pickup_point.name, 12) }}
                </text>
                <text :x="getPointPos(i).x" :y="getPointPos(i).y + 46"
                      text-anchor="middle" font-size="11" fill="#909399">
                  {{ p.distance_km }}km · {{ p.order_count }}单
                </text>
              </template>
            </svg>
            <el-empty v-else description="暂无送货数据" :image-size="80" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <el-icon :size="18" color="#67c23a"><List /></el-icon>
                <span style="font-weight: 600; font-size: 15px;">送货顺序清单</span>
              </div>
              <div style="display: flex; align-items: center; gap: 8px; font-size: 12px;">
                <el-tag size="small" type="warning">未打包</el-tag>
                <el-tag size="small" type="primary">已生成</el-tag>
                <el-tag size="small" type="success">已装车</el-tag>
              </div>
            </div>
          </template>

          <el-empty v-if="!routeData || routeData.route.length === 0" description="当日暂无送货安排" />

          <el-timeline v-else style="padding: 10px 0;">
            <el-timeline-item
              type="danger"
              size="large"
              :timestamp="'出发'"
              timestamp-placement="top"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <div style="font-weight: 600; font-size: 15px; color: #ff6b6b;">
                    <el-icon><OfficeBuilding /></el-icon>
                    中央仓库
                  </div>
                  <div style="font-size: 12px; color: #909399; margin-top: 2px;">
                    坐标: {{ routeData.warehouse_lat }}, {{ routeData.warehouse_lng }}
                  </div>
                </div>
                <el-tag type="danger" size="large">起点</el-tag>
              </div>
            </el-timeline-item>

            <template v-for="(p, i) in routeData.route" :key="p.pickup_point.id">
              <el-timeline-item
                :type="getStatusType(p.status)"
                size="large"
                :timestamp="`第 ${p.sequence} 站 · 距起点 ${p.distance_km} km`"
                timestamp-placement="top"
                :hollow="!p.status || p.status === 'created'"
              >
                <el-card shadow="never" :body-style="{ padding: '14px 16px' }" style="border-color: #ebeef5;">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                      <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 15px; font-weight: 600; color: #303133;">
                          {{ p.pickup_point.name }}
                        </span>
                        <el-tag v-if="!p.status" type="warning" size="small">待打包</el-tag>
                        <el-tag v-else-if="p.status === 'created'" type="primary" size="small" effect="plain">已生成</el-tag>
                        <el-tag v-else-if="p.status === 'printed'" type="info" size="small">已打印</el-tag>
                        <el-tag v-else-if="p.status === 'loaded'" type="success" size="small" effect="dark">已装车</el-tag>
                      </div>

                      <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px; font-size: 13px;">
                        <div style="color: #606266;">
                          <el-icon :size="14"><Location /></el-icon>
                          {{ p.pickup_point.address }}
                        </div>
                        <div style="color: #606266;">
                          <el-icon :size="14"><User /></el-icon>
                          团长: {{ p.pickup_point.leader?.name || '-' }}
                          <el-tag size="small" type="info" style="margin-left: 6px;">
                            {{ p.pickup_point.leader?.phone || '-' }}
                          </el-tag>
                        </div>
                        <div v-if="p.slip_no" style="color: #606266;">
                          <el-icon :size="14"><Document /></el-icon>
                          配货单: <span style="font-family: monospace;">{{ p.slip_no }}</span>
                        </div>
                      </div>
                    </div>

                    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px; margin-left: 16px;">
                      <div style="display: flex; gap: 12px;">
                        <div style="text-align: center;">
                          <div style="font-size: 10px; color: #909399;">订单</div>
                          <div style="font-size: 18px; font-weight: 600; color: #409eff;">{{ p.order_count }}</div>
                        </div>
                        <div style="text-align: center;">
                          <div style="font-size: 10px; color: #909399;">件数</div>
                          <div style="font-size: 18px; font-weight: 600; color: #67c23a;">{{ p.total_items }}</div>
                        </div>
                      </div>
                      <div v-if="p.status && p.status !== 'loaded'" style="margin-top: 4px;">
                        <el-button
                          size="small"
                          type="success"
                          :icon="Van"
                          :disabled="updatingId === p.packing_slip_id"
                          @click="markAsLoaded(p)"
                        >
                          标记已装车
                        </el-button>
                      </div>
                      <div v-else-if="p.status === 'loaded'" style="margin-top: 4px;">
                        <el-tag type="success" effect="dark" size="small" round>
                          <el-icon><Check /></el-icon>
                          已装车
                        </el-tag>
                      </div>
                    </div>
                  </div>

                  <el-divider direction="vertical" v-if="i < (routeData?.route?.length || 0) - 1" style="display: none;" />
                </el-card>
              </el-timeline-item>
            </template>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh, MapLocation, List, Van, User, Location,
  OfficeBuilding, Document, Check
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getDeliveryRoute, getRouteWithoutPacking, updatePackingSlipStatus } from '../api'

const deliveryDate = ref(dayjs().format('YYYY-MM-DD'))
const includeUnpacked = ref(true)
const routeData = ref(null)
const updatingId = ref(null)

const warehousePos = { x: 210, y: 50 }

const totalOrderCount = computed(() =>
  (routeData.value?.route || []).reduce((s, p) => s + (p.order_count || 0), 0)
)

function getStatusType(status) {
  if (!status) return 'warning'
  if (status === 'loaded') return 'success'
  if (status === 'printed') return 'info'
  return 'primary'
}

function truncateText(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
}

function getPointPos(index) {
  const total = routeData.value?.route?.length || 1
  const startY = 150
  const spacing = Math.min(80, (500 - startY) / Math.max(total, 1))
  const baseX = 210
  const offsetX = index % 2 === 0 ? -70 : 70
  return {
    x: baseX + (total > 1 ? offsetX * (index / (total - 1 || 1)) * 0.6 : 0),
    y: startY + index * spacing
  }
}

async function loadData() {
  try {
    const fn = includeUnpacked.value ? getRouteWithoutPacking : getDeliveryRoute
    routeData.value = await fn({
      delivery_date: deliveryDate.value
    })
  } catch (e) {
    console.error(e)
  }
}

async function markAsLoaded(point) {
  if (!point.packing_slip_id) return
  updatingId.value = point.packing_slip_id
  try {
    await updatePackingSlipStatus(point.packing_slip_id, 'loaded')
    ElMessage.success(`第 ${point.sequence} 站 [${point.pickup_point.name}] 已标记装车`)
    await loadData()
  } catch (e) {
    console.error(e)
  } finally {
    updatingId.value = null
  }
}

onMounted(() => {
  loadData()
})
</script>
