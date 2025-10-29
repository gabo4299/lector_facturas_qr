export interface  Category {
    id:number;
    nombre:string
    descripcion?:string
}

export interface Batch {
nombre: string;
descripcion: string;
id: number;
proyecto_id: number;

}
export interface MediaTrackCapabilities {
  torch?: boolean;
}
export interface BatchResume {
  batch_info:Batch;
  monto_total_batch?: number
  cantidad_manuales?:number
  cantidad_electronicas?:number
}

export interface UserProject {
  id:number;
  name:string;
  email?:string;
  is_superuser?:boolean;
}
export interface asociacionProyecto {
  usuario:UserProject;
  rol:string
}

export interface ProjectInfo {
  id: number;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  nit_beneficiario: string;
  suma_total: number;
  cantidad_facturas_electronicas: number;
  cantidad_facturas_manuales: number;
  porcentajeGanado:number;
  suma_facturas_electronicas?:number
  suma_facturas_manuales?:number
  batches:BatchResume[]|Batch[];
  
  asociaciones_usuario?:[asociacionProyecto]
  propietario?:UserProject
  // ... y cualquier otro campo que necesites
}


export interface ProjectInfoDetail {
  id: number;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  nit_beneficiario: string;
  suma_total: number;
  cantidad_facturas_electronicas: number;
  cantidad_facturas_manuales: number;
  porcentajeGanado:number;
  suma_facturas_electronicas?:number
  suma_facturas_manuales?:number
  batches:BatchResume[];
  
  asociaciones_usuario?:[asociacionProyecto]
  propietario?:UserProject
  // ... y cualquier otro campo que necesites
}
export interface ProjectAdmin {
  id: number;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  nit_beneficiario: string;
  total_facturas?: number;
  suma_total_facturas?:number
  asociaciones_usuario?:[asociacionProyecto]
  propietario?:UserProject
  batches?:Batch[];
  // ... y cualquier otro campo que necesites
}


export interface addMemberToProject {
  email: string;
  rol:string;
  
}

export interface Company {
  id: number;
  nombre: string;
  nit?: string;
  rubro?:string;
}


export interface CompanyResume {
  empresa_info: Company;
  monto_total_empresa?: number;
  cantidad_manuales?: number;
  cantidad_electronicas?:number;
}

export interface CategoryResume {
  categoria_info: Category;
  monto_total_categoria?: number;
  cantidad_manuales?: number;
  cantidad_electronicas?:number;
}



export interface ManualInvoiceAPI {
  id: number;
  fecha: string;
  empresa: Company | null;
  monto_total: number;
  batch: Batch | null;
  categoria: Category | null;
  proyecto?:ProjectAdmin|ProjectInfo
}
export interface ElectronicInvoiceAPI {
  id: number;
  fecha: string;
  url?:string;
  empresa: Company | null;
  monto_total: number;
  monto_fiscal: number;
  batch: Batch | null;
  categoria: Category | null;
  factura_especial:boolean|null;
   status: string;
   save_pdf:boolean;
   complete:boolean;
   proyecto?:ProjectAdmin|ProjectInfo
}


export interface ProjectResume { // Solo datos del proyecto
  id: number;
  nombre: string;
  fecha_inicio: Date;
  fecha_fin:Date;
  nit_beneficiario:string;
  suma_total:number;
  cantidad_facturas_electronicas:number;
  cantidad_facturas_manuales:number;
  suma_facturas_electronicas:number;
  suma_facturas_manuales:number;
  porcentajeGanado:number;
  batches:BatchResume[];
  categorias:CategoryResume[];
  empresas:CompanyResume[];


  // ... otros campos del proyecto
}