<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">分拣配货</h2>
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
        <el-button type="primary" :icon="Refresh" @click="loadData">刷新</el-button>
      </div>
    </div>

    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <div class="stat-label" style="color: rgba(255,255,255,0.85);">待配货自提点</div>
          <div class="stat-value" style="color: #fff;">{{ groupedData.length }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <div class="stat-label" style="color: rgba(255,255,255,0.85);">待处理订单</div>
          <div class="stat-value" style="color: #fff;">{{ totalOrders }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <div class="stat-label" style="color: rgba(255,255,255,0.85);">商品种类数</div>
          <div class="stat-value" style="color: #fff;">{{ totalProducts }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <div class="stat-label" style="color: rgba(255,255,255,0.85);">已生成配货单</div>
          <div class="stat-value" style="color: #fff;">{{ packedCount }}</div>
        </div>
      </el-col>
    </el-row>

    <el-empty v-if="loading === false && groupedData.length === 0" description="当日暂无待配货订单" />

    <el-row v-else :gutter="16">
      <el-col v-for="(group, idx) in groupedData" :key="group.pickup_point_id" :span="24" style="margin-bottom: 16px;">
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <el-tag type="warning" size="large" :effect="isPacked(group.pickup_point_id) ? 'dark' : 'light'">
                  {{ idx + 1 }}
                </el-tag>
                <div>
                  <div style="font-size: 16px; font-weight: 600; color: #303133;">
                    {{ group.pickup_point_name }}
                    <el-tag v-if="isPacked(group.pickup_point_id)" type="success" size="small" style="margin-left: 8px;">
                      已打包
                    </el-tag>
                  </div>
                  <div style="font-size: 13px; color: #909399; margin-top: 4px;">
                    <el-icon :size="14"><Location /></el-icon>
                    {{ group.address }}
                    <span style="margin: 0 8px; color: #dcdfe6;">|</span>
                    <el-icon :size="14"><User /></el-icon>
                    {{ group.leader_name }} ({{ group.leader_phone }})
                  </div>
                </div>
              </div>
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="text-align: right;">
                  <div style="color: #909399; font-size: 12px;">订单数</div>
                  <div style="font-size: 20px; font-weight: 600; color: #409eff;">{{ group.order_count }}</div>
                </div>
                <div style="text-align: right;">
                  <div style="color: #909399; font-size: 12px;">商品种类</div>
                  <div style="font-size: 20px; font-weight: 600; color: #67c23a;">{{ group.product_summary.length }}</div>
                </div>
                <el-button
                  type="success"
                  :icon="Printer"
                  @click="openPackingDialog(group)"
                  :disabled="isPacked(group.pickup_point_id)"
                >
                  生成配货单
                </el-button>
              </div>
            </div>
          </template>

          <el-tabs v-model="group._activeTab">
            <el-tab-pane label="商品汇总" name="summary">
              <el-table :data="group.product_summary" size="small" stripe>
                <el-table-column label="序号" type="index" width="60" align="center" />
                <el-table-column prop="sku" label="商品编码" width="120" />
                <el-table-column prop="product_name" label="商品名称" min-width="160" />
                <el-table-column label="总数量" width="140" align="center">
                  <template #default="{ row }">
                    <span style="font-size: 16px; font-weight: 600; color: #e6a23c;">
                      {{ formatQty(row.total_quantity) }}
                    </span>
                    <span style="color: #909399; margin-left: 4px;">{{ row.unit }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="分拣状态" width="120" align="center">
                  <template #default="{ row, $index }">
                    <el-checkbox
                      :model-value="checkedItems[`${group.pickup_point_id}-${$index}`]"
                      @change="(v) => toggleItemCheck(group.pickup_point_id, $index, v)"
                    >
                      已分拣
                    </el-checkbox>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <el-tab-pane :label="`订单明细 (${group.orders.length})`" name="orders">
              <el-collapse accordion>
                <el-collapse-item
                  v-for="order in group.orders"
                  :key="order.order_id"
                  :name="order.order_id"
                >
                  <template #title>
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; padding-right: 20px;">
                      <div style="display: flex; align-items: center; gap: 16px;">
                        <el-tag type="info">{{ order.order_no }}</el-tag>
                        <span style="font-weight: 500;">{{ order.customer_name }}</span>
                        <span style="color: #909399;">{{ order.customer_phone }}</span>
                        <el-tag v-if="order.remark" type="warning" size="small" effect="plain">
                          <el-icon><Warning /></el-icon>
                          {{ order.remark }}
                        </el-tag>
                      </div>
                      <span style="color: #67c23a; font-size: 13px;">{{ order.items.length }} 件商品</span>
                    </div>
                  </template>
                  <el-table :data="order.items" size="small" style="margin-top: -20px;">
                    <el-table-column label="序号" type="index" width="60" align="center" />
                    <el-table-column prop="product_name" label="商品名称" min-width="180" />
                    <el-table-column label="数量" width="160" align="center">
                      <template #default="{ row }">
                        <span style="font-weight: 500; color: #409eff;">
                          {{ formatQty(row.quantity) }}
                        </span>
                        <span style="color: #909399; margin-left: 4px;">{{ row.unit }}</span>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-collapse-item>
              </el-collapse>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="packingDialogVisible" title="确认配货单信息" width="650px">
      <div v-if="currentGroup" style="padding: 0 10px;">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="自提点" :span="2">
            {{ currentGroup.pickup_point_name }}
          </el-descriptions-item>
          <el-descriptions-item label="配送地址">{{ currentGroup.address }}</el-descriptions-item>
          <el-descriptions-item label="团长">
            {{ currentGroup.leader_name }} ({{ currentGroup.leader_phone }})
          </el-descriptions-item>
          <el-descriptions-item label="订单数">{{ currentGroup.order_count }} 单</el-descriptions-item>
          <el-descriptions-item label="商品种类">{{ currentGroup.product_summary.length }} 种</el-descriptions-item>
          <el-descriptions-item label="配送日期" :span="2">{{ deliveryDate }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">商品清单</el-divider>
        <el-table :data="currentGroup.product_summary" size="small" border>
          <el-table-column label="序号" type="index" width="60" align="center" />
          <el-table-column prop="sku" label="编码" width="100" />
          <el-table-column prop="product_name" label="商品名称" min-width="160" />
          <el-table-column label="数量" width="120" align="center">
            <template #default="{ row }">
              <strong style="color: #e6a23c;">{{ formatQty(row.total_quantity) }}</strong>
              <span style="color: #909399; margin-left: 2px;">{{ row.unit }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="packingDialogVisible = false">取消</el-button>
        <el-button type="success" :icon="Check" :loading="submitting" @click="submitPackingSlip">
          确认生成配货单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh, Printer, Check, Location, User, Warning
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getGroupedOrders, listPackingSlips, createPackingSlip } from '../api'

const loading = ref(false)
const deliveryDate = ref(dayjs().format('YYYY-MM-DD'))
const groupedData = ref([])
const packingSlips = ref([])
const checkedItems = reactive({})

const packingDialogVisible = ref(false)
const currentGroup = ref(null)
const submitting = ref(false)

const totalOrders = computed(() =>
  groupedData.value.reduce((s, g) => s + g.order_count, 0)
)

const totalProducts = computed(() =>
  groupedData.value.reduce((s, g) => s + g.product_summary.length, 0)
)

const packedCount = computed(() =>
  groupedData.value.filter(g => isPacked(g.pickup_point_id)).length
)

function formatQty(qty) {
  return Number.isInteger(qty) ? qty.toString() : qty.toFixed(1)
}

function isPacked(pointId) {
  return packingSlips.value.some(s => s.pickup_point_id === pointId)
}

function toggleItemCheck(pointId, index, value) {
  checkedItems[`${pointId}-${index}`] = value
}

async function loadData() {
  loading.value = true
  try {
    const [grouped, slips] = await Promise.all([
      getGroupedOrders(deliveryDate.value),
      listPackingSlips({ delivery_date: deliveryDate.value })
    ])
    groupedData.value = (grouped || []).map(g => ({ ...g, _activeTab: 'summary' }))
    packingSlips.value = slips || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openPackingDialog(group) {
  currentGroup.value = group
  packingDialogVisible.value = true
}

async function submitPackingSlip() {
  if (!currentGroup.value) return
  submitting.value = true
  try {
    const orderIds = currentGroup.value.orders.map(o => o.order_id)
    await createPackingSlip({
      pickup_point_id: currentGroup.value.pickup_point_id,
      delivery_date: deliveryDate.value,
      order_ids: orderIds
    })
    ElMessage.success(`配货单生成成功！共 ${orderIds.length} 单`)
    packingDialogVisible.value = false
    await loadData()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
