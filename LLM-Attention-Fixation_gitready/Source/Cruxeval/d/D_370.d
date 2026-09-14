import std.math;
import std.typecons;
import std.ascii;

bool f(string text) 
{
    foreach (char c; text) {
        if (!c.isWhite) {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("     i") == false);
}
void main(){}
