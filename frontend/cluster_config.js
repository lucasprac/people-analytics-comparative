// Clustering module (disabled by default)
export const CLUSTERING_ENABLED = false;

export function prepareClusteringRequest(quarter, by){
  if(!CLUSTERING_ENABLED){
    throw new Error('Clustering está desativado por configuração.');
  }
  return { quarter, by };
}
