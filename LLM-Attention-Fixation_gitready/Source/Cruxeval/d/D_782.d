import std.math;
import std.typecons;
import std.ascii;

bool f(string input) 
{
    foreach (char c; input) {
        if (isUpper(c)) {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("a j c n x X k") == false);
}
void main(){}
