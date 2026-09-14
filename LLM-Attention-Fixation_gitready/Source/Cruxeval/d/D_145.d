import std.algorithm;
import std.math;
import std.typecons;
import std.array;

float f(float price, string product) 
{
    auto inventory = ["olives", "key", "orange"];
    if (!inventory.canFind(product))
    {
        return price;
    }
    else
    {
        price *= 0.85;
        inventory.remove(product);
    }
    return price;
}
unittest
{
    alias candidate = f;

    assert(candidate(8.5, "grapes") == 8.5);
}
void main(){}
