import std.math;
import std.typecons;

Tuple!(string, string) f(string a, string b) 
{
    if (a < b)
    {
        return tuple(b, a);
    }
    return tuple(a, b);
}
unittest
{
    alias candidate = f;

    assert(candidate("ml", "mv") == tuple("mv", "ml"));
}
void main(){}
