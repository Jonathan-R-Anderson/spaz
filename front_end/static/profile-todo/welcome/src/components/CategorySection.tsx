
import { Button } from "@/components/ui/button";

// Mock data for categories
const categories = [
  {
    id: 1,
    name: "Crypto",
    viewers: 58900,
    image: "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?q=80&w=200&h=280&auto=format&fit=crop"
  },
  {
    id: 2,
    name: "NFT Art",
    viewers: 42300,
    image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=200&h=280&auto=format&fit=crop"
  },
  {
    id: 3,
    name: "Gaming",
    viewers: 37600,
    image: "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=200&h=280&auto=format&fit=crop"
  },
  {
    id: 4,
    name: "Development",
    viewers: 28400,
    image: "https://images.unsplash.com/photo-1555099962-4199c345e5dd?q=80&w=200&h=280&auto=format&fit=crop"
  },
  {
    id: 5,
    name: "DAOs",
    viewers: 19700,
    image: "https://images.unsplash.com/photo-1639322537087-2c8ada5bbf2f?q=80&w=200&h=280&auto=format&fit=crop"
  },
  {
    id: 6,
    name: "Metaverse",
    viewers: 17200,
    image: "https://images.unsplash.com/photo-1633356122102-3fe601e05bd2?q=80&w=200&h=280&auto=format&fit=crop"
  }
];

const CategorySection = () => {
  return (
    <section className="py-10">
      <div className="container mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Popular Categories</h2>
          <Button variant="ghost" className="text-web3-primary hover:text-web3-accent hover:bg-web3-accent/10">
            View All
          </Button>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {categories.map((category) => (
            <div key={category.id} className="relative rounded-lg overflow-hidden group cursor-pointer">
              <img
                src={category.image}
                alt={category.name}
                className="w-full h-[280px] object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-4">
                <h3 className="text-lg font-semibold text-white">{category.name}</h3>
                <p className="text-sm text-web3-textMuted">
                  {new Intl.NumberFormat().format(category.viewers)} viewers
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CategorySection;
