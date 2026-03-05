// Código para conectar tu App de Android con Firebase
val database = FirebaseDatabase.getInstance().getReference("predicciones")

database.addValueEventListener(object : ValueEventListener {
    override fun onDataChange(snapshot: DataSnapshot) {
        if (snapshot.exists()) {
            // Extraemos los datos que envió Python
            val partido = snapshot.child("partido").value.toString()
            val ganador = snapshot.child("ganador").value.toString()
            
            // Actualizamos la interfaz del celular
            txt_partido.text = partido
            txt_resultado.text = "IA Predice: Gana $ganador"
        }
    }

    override fun onCancelled(error: DatabaseError) {
        Log.e("FirebaseError", error.message)
    }
})
