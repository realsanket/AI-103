variable "location" {
  description = "Azure region for this independently deployable production cell."
  type        = string
}

variable "resource_group_name" {
  description = "Existing or new resource group name for this production cell."
  type        = string
}

variable "prefix" {
  description = "Lowercase production-cell prefix used for non-global names."
  type        = string
}

variable "foundry_name" {
  description = "Globally unique lowercase Microsoft Foundry account name."
  type        = string
}

variable "project_name" {
  description = "Foundry project name. No model deployment is created."
  type        = string
  default     = "production"
}

variable "key_vault_name" {
  description = "Globally unique lowercase Key Vault name in same region as Foundry."
  type        = string
}

variable "storage_account_name" {
  description = "Globally unique lowercase Storage account name."
  type        = string
}

variable "vnet_address_space" {
  description = "RFC 1918 CIDR for VNet."
  type        = string
  default     = "10.42.0.0/16"
}

variable "private_endpoint_subnet_prefix" {
  description = "CIDR for private endpoints."
  type        = string
  default     = "10.42.1.0/24"
}

variable "agent_subnet_prefix" {
  description = "Dedicated Foundry Agent Service VNet-injection CIDR; /27 minimum."
  type        = string
  default     = "10.42.2.0/24"
}

variable "assign_connection_policy" {
  description = "Set true only after nonproduction policy validation."
  type        = bool
  default     = false
}

variable "allowed_connection_categories" {
  description = "Foundry connection categories approved by your platform."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Required operational ownership tags."
  type        = map(string)
  default = {
    environment = "production"
    managed-by  = "terraform"
  }
}
