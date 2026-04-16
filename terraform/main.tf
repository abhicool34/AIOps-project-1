resource "helm_release" "fluent_bit" {
  name       = "fluent-bit"
  repository = "https://fluent.github.io/helm-charts"
  chart      = "fluent-bit"
  namespace  = kubernetes_namespace.dev_env.metadata[0].name

  values = [
    file("${path.module}/helm/fluent-bit-values.yaml")
  ]
}