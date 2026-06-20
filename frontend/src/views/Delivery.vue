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
      <el-col :span="14">
        <el-card shadow="hover" class="map-card">
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px;">
              <el-icon :size="18" color="#409eff"><MapLocation /></el-icon>
              <span style="font-weight: 600; font-size: 15px;">配送路线地图</span>
              <el-tag v-if="routeData && routeData.route.length > 0" type="info" size="small" style="margin-left: 8px;">
                点击地图上的标号可查看详情
              </el-tag>
            </div>
          </template>
          <div class="map-wrapper">
            <div v-if="!routeData || routeData.route.length === 0" class="map-empty">
              <el-empty description="当日暂无送货安排" :image-size="80" />
            </div>
            <l-map
              v-else
              ref="mapRef"
              :zoom="12"
              :center="mapCenter"
              :useGlobalLeaflet="false"
              class="leaflet-map"
            >
              <l-tile-layer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                layer-type="base"
                name="OpenStreetMap"
              />

              <l-polyline :lat-lngs="polylinePoints" :color="'#409eff'" :weight="4" :opacity="0.85" :dash-array="'8, 8'">
              </l-polyline>

              <l-marker
                :lat-lng="[routeData.warehouse_lat, routeData.warehouse_lng]"
                :icon="warehouseIcon"
              >
                <l-popup>
                  <div class="popup-content">
                    <div class="popup-title warehouse">
                      <el-icon><OfficeBuilding /></el-icon>
                      中央仓库（起点）
                    </div>
                    <div class="popup-info">坐标: {{ routeData.warehouse_lat }}, {{ routeData.warehouse_lng }}</div>
                  </div>
                </l-popup>
              </l-marker>

              <l-marker
                v-for="(p, index) in routeData.route"
                :key="p.pickup_point.id"
                :lat-lng="[p.pickup_point.latitude, p.pickup_point.longitude]"
                :icon="getPointIcon(p, index)"
                @click="activePointIndex = index"
              >
                <l-popup>
                  <div class="popup-content">
                    <div class="popup-title">
                      <span class="seq-badge" :class="getStatusClass(p.status)">{{ p.sequence }}</span>
                      <span class="name-text">{{ p.pickup_point.name }}</span>
                    </div>
                    <div class="popup-info">
                      <div><span class="label">地址:</span> {{ p.pickup_point.address }}</div>
                      <div><span class="label">团长:</span> {{ p.pickup_point.leader?.name || '-' }} ({{ p.pickup_point.leader?.phone || '-' }})</div>
                      <div><span class="label">订单:</span> {{ p.order_count }} 单 / {{ p.total_items }} 件</div>
                      <div><span class="label">距仓库:</span> {{ p.distance_km }} km</div>
                      <div v-if="p.slip_no"><span class="label">配货单:</span> {{ p.slip_no }}</div>
                      <div>
                        <span class="label">状态:</span>
                        <el-tag size="small" :type="getStatusTag(p.status)">
                          {{ statusText(p.status) }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </l-popup>
              </l-marker>

              <l-control position="bottomright" class="legend-control">
                <div class="map-legend">
                  <div class="legend-title">图例</div>
                  <div class="legend-item">
                    <span class="legend-marker warehouse-marker">仓</span>
                    <span>仓库起点</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-marker num-marker">1</span>
                    <span>送货点（按顺序）</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-line"></span>
                    <span>配送路线</span>
                  </div>
                </div>
              </l-control>
            </l-map>
          </div>
        </el-card>
      </el-col>

      <el-col :span="10">
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
              timestamp="出发"
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
                @click="focusOnPoint(i)"
                style="cursor: pointer;"
              >
                <el-card
                  shadow="never"
                  :body-style="{ padding: '14px 16px' }"
                  :class="['point-card', activePointIndex === i ? 'active' : '']"
                >
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
                          @click.stop="markAsLoaded(p)"
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh, MapLocation, List, Van, User, Location,
  OfficeBuilding, Document, Check
} from '@element-plus/icons-vue'
import { LMap, LTileLayer, LMarker, LPopup, LPolyline, LControl } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import dayjs from 'dayjs'
import { getDeliveryRoute, getRouteWithoutPacking, updatePackingSlipStatus } from '../api'

const deliveryDate = ref(dayjs().format('YYYY-MM-DD'))
const includeUnpacked = ref(true)
const routeData = ref(null)
const updatingId = ref(null)
const mapRef = ref(null)
const activePointIndex = ref(-1)

const defaultCenter = [39.9042, 116.4074]
const mapCenter = ref(defaultCenter)

const totalOrderCount = computed(() =>
  (routeData.value?.route || []).reduce((s, p) => s + (p.order_count || 0), 0)
)

const polylinePoints = computed(() => {
  if (!routeData.value || !routeData.value.route.length) return []
  const points = [[routeData.value.warehouse_lat, routeData.value.warehouse_lng]]
  routeData.value.route.forEach(p => {
    points.push([p.pickup_point.latitude, p.pickup_point.longitude])
  })
  return points
})

function createNumberedIcon(num, status) {
  const color = status === 'loaded' ? '#67c23a' : status ? '#409eff' : '#e6a23c'
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="52" viewBox="0 0 40 52">
      <path d="M20 0 C9 0 0 9 0 20 C0 32 12 44 20 52 C28 44 40 32 40 20 C40 9 31 0 20 0 Z"
            fill="${color}" stroke="#fff" stroke-width="2"/>
      <circle cx="20" cy="19" r="12" fill="#fff"/>
      <text x="20" y="24" text-anchor="middle" font-size="14" font-weight="bold" fill="${color}">${num}</text>
    </svg>
  `
  return L.divIcon({
    className: 'numbered-marker',
    html: svg,
    iconSize: [40, 52],
    iconAnchor: [20, 52],
    popupAnchor: [0, -48]
  })
}

const warehouseIcon = L.divIcon({
  className: 'warehouse-marker-icon',
  html: `
    <svg xmlns="http://www.w3.org/2000/svg" width="44" height="56" viewBox="0 0 44 56">
      <path d="M22 0 C10 0 0 10 0 22 C0 35 13 48 22 56 C31 48 44 35 44 22 C44 10 34 0 22 0 Z"
            fill="#ff4d4f" stroke="#fff" stroke-width="2"/>
      <circle cx="22" cy="21" r="13" fill="#fff"/>
      <text x="22" y="27" text-anchor="middle" font-size="14" font-weight="bold" fill="#ff4d4f">仓</text>
    </svg>
  `,
  iconSize: [44, 56],
  iconAnchor: [22, 56],
  popupAnchor: [0, -52]
})

function getPointIcon(p, index) {
  return createNumberedIcon(p.sequence, p.status)
}

function getStatusType(status) {
  if (!status) return 'warning'
  if (status === 'loaded') return 'success'
  if (status === 'printed') return 'info'
  return 'primary'
}

function getStatusTag(status) {
  if (!status) return 'warning'
  if (status === 'loaded') return 'success'
  if (status === 'printed') return 'info'
  return 'primary'
}

function getStatusClass(status) {
  if (!status) return 'warning'
  if (status === 'loaded') return 'success'
  if (status === 'printed') return 'info'
  return 'primary'
}

function statusText(status) {
  if (!status) return '待打包'
  if (status === 'created') return '已生成'
  if (status === 'printed') return '已打印'
  if (status === 'loaded') return '已装车'
  return status
}

function focusOnPoint(index) {
  activePointIndex.value = index
  if (mapRef.value && routeData.value && routeData.value.route[index]) {
    const p = routeData.value.route[index]
    mapRef.value.leafletObject.setView([p.pickup_point.latitude, p.pickup_point.longitude], 14)
  }
}

function fitMapBounds() {
  if (!mapRef.value || !routeData.value || !routeData.value.route.length) return
  const bounds = []
  bounds.push([routeData.value.warehouse_lat, routeData.value.warehouse_lng])
  routeData.value.route.forEach(p => {
    bounds.push([p.pickup_point.latitude, p.pickup_point.longitude])
  })
  nextTick(() => {
    if (mapRef.value) {
      mapRef.value.leafletObject.fitBounds(bounds, { padding: [60, 60] })
    }
  })
}

async function loadData() {
  try {
    const fn = includeUnpacked.value ? getRouteWithoutPacking : getDeliveryRoute
    routeData.value = await fn({
      delivery_date: deliveryDate.value
    })
    if (routeData.value && routeData.value.route.length > 0) {
      mapCenter.value = [routeData.value.warehouse_lat, routeData.value.warehouse_lng]
    }
    nextTick(() => {
      fitMapBounds()
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

watch(
  () => routeData.value?.route?.length,
  () => {
    fitMapBounds()
  }
)

onMounted(() => {
  loadData()
})
</script>

<style>
.leaflet-map {
  width: 100%;
  height: 600px;
  border-radius: 6px;
}

.map-card .el-card__body {
  padding: 0 !important;
}

.map-wrapper {
  position: relative;
}

.map-empty {
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.numbered-marker {
  background: transparent !important;
  border: none !important;
}

.warehouse-marker-icon {
  background: transparent !important;
  border: none !important;
}

.popup-content {
  min-width: 220px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.popup-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.popup-title.warehouse {
  color: #ff4d4f;
}

.seq-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
}
.seq-badge.primary { background: #409eff; }
.seq-badge.success { background: #67c23a; }
.seq-badge.warning { background: #e6a23c; }
.seq-badge.info    { background: #909399; }

.name-text {
  font-size: 14px;
}

.popup-info {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.popup-info .label {
  color: #909399;
  margin-right: 4px;
}

.point-card {
  transition: all 0.2s ease;
  border-color: #ebeef5;
}

.point-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateX(4px);
}

.point-card.active {
  border-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.3);
  transform: translateX(4px);
}

.map-legend {
  background: rgba(255, 255, 255, 0.95);
  padding: 10px 14px;
  border-radius: 6px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.15);
  font-size: 12px;
  color: #606266;
}

.legend-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
  font-size: 13px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.legend-marker {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 28px;
  font-size: 10px;
  font-weight: bold;
  color: #fff;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
}

.legend-marker.warehouse-marker {
  background: #ff4d4f;
}

.legend-marker.num-marker {
  background: #409eff;
}

.legend-marker span {
  transform: rotate(45deg);
}

.legend-line {
  width: 24px;
  height: 3px;
  background: repeating-linear-gradient(to right, #409eff 0, #409eff 6px, transparent 6px, transparent 10px);
  border-radius: 2px;
}

.leaflet-control-attribution {
  font-size: 10px !important;
}
</style>
