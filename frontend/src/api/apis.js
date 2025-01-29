import service from './service';

export const getInstruction = (params, modelType) => {
  return service({
    url: `/getInstruction/${modelType}`,
    method: 'post',
    data: params
  });
}

export const operateDrone = (params) => {
  return service({
    url: '/operateDrone',
    method: 'post',
    data: params
  });
}