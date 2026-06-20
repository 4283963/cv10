<template>
  <el-container>
    <el-aside width="220px" style="background: #001529;">
      <div class="logo">
        <el-icon :size="28" color="#67c23a"><Shop /></el-icon>
        <span>生鲜配货系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#001529"
        text-color="#c9d1d9"
        active-text-color="#67c23a"
        router
        style="border-right: none;"
      >
        <el-menu-item index="/packing">
          <el-icon><Box /></el-icon>
          <span>分拣配货</span>
        </el-menu-item>
        <el-menu-item index="/delivery">
          <el-icon><Van /></el-icon>
          <span>送货指引</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #e4e7ed; display: flex; align-items: center; justify-content: space-between;">
        <div style="font-size: 16px; font-weight: 500; color: #303133;">
          {{ $route.meta.title || '首页' }}
        </div>
        <div style="display: flex; align-items: center; gap: 8px; color: #606266;">
          <el-icon><User /></el-icon>
          <span>仓库管理员</span>
        </div>
      </el-header>
      <el-main style="background: #f5f7fa; padding: 20px;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 17px;
  font-weight: 600;
  border-bottom: 1px solid #0d2136;
}

.el-menu-item {
  height: 52px;
  line-height: 52px;
}
</style>
