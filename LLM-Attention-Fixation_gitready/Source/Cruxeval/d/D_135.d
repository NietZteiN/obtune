import std.math;
import std.typecons;
import std.array;

string[] f() 
{
    auto d = ["Russia": [tuple("Moscow", "Russia"), tuple("Vladivostok", "Russia")],
              "Kazakhstan": [tuple("Astana", "Kazakhstan")]];
    return d.keys;
}
unittest
{
    alias candidate = f;

    assert(candidate() == ["Russia", "Kazakhstan"]);
}
void main(){}
