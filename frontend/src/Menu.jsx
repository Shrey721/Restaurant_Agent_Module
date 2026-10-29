export default function Menu({ items, onPick }) {
  // group dishes by category
  const categories = {};
  for (const item of items) {
    if (!categories[item.category]) categories[item.category] = [];
    categories[item.category].push(item);
  }

  return (
    <aside className="menu">
      <h2>Menu</h2>
      {Object.entries(categories).map(([category, dishes]) => (
        <div key={category}>
          <h3>{category}</h3>
          {dishes.map((dish) => (
            <button key={dish.name} className="dish" onClick={() => onPick(dish.name)} title={dish.components}>
              <span>{dish.name}</span>
              <span className="price">₹{dish.price}</span>
            </button>
          ))}
        </div>
      ))}
    </aside>
  );
}
