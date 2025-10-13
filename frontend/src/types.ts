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
  monto_total_batch: number
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
  batches:[BatchResume];
  asociaciones_usuario?:[asociacionProyecto]
  propietario?:UserProject

  // ... y cualquier otro campo que necesites
}


export interface addMemberToProject {
  email: string;
  rol:string;
  
}

export interface Company {
  id: number;
  nombre: string;
  nit: string;
  rubro?:string;
}