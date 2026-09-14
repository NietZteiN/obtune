import std.math;
import std.typecons;
import std.ascii;

bool f(string s) 
{
    auto l = s.dup;
    foreach(i; 0 .. l.length) {
        l[i] = toLower(l[i]);
        if (!isDigit(l[i])) {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("") == true);
}
void main(){}
