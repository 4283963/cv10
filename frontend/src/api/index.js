import request from './request'

export const listPickupPoints = () => request.get('/pickup-points')

export const listProducts = (params) => request.get('/products', { params })

export const listOrders = (params) => request.get('/orders', { params })

export const createOrder = (data) => request.post('/orders', data)

export const getGroupedOrders = (delivery_date) =>
  request.get('/packing-slips/grouped/by-pickup-point', { params: { delivery_date } })

export const listPackingSlips = (params) =>
  request.get('/packing-slips', { params })

export const createPackingSlip = (data) => request.post('/packing-slips', data)

export const updatePackingSlipStatus = (id, status) =>
  request.patch(`/packing-slips/${id}/status`, null, { params: { status } })

export const getDeliveryRoute = (params) =>
  request.get('/delivery/route', { params })

export const getRouteWithoutPacking = (params) =>
  request.get('/delivery/route-without-packing', { params })
