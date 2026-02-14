const Cart = () => {
  return (
    // Padding TOP pour rester en dessous du menu (à voir si on encapsule le menu dans header pour éviter d'avoir à faire ça)
    <div className="min-h-screen pt-40 px-4 md:px-8">

      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-heading  mb-6 pb-2 border-b border-teal-900 dark:border-primary">Mon Panier</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="text-muted-foreground">Chargement du panier...</div>
        </div>
      </div>

    </div>
  );
};

export default Cart;