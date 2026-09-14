import std.math;
import std.typecons;
import std.range;

bool f(string w) 
{
    auto ls = w.dup;
    string omw = "";
    while (ls.length > 0) {
        omw ~= ls.front;
        ls.popFront();
        if (ls.length * 2 > w.length && w[ls.length..$] == omw) {
            return true;
        }
    }
    return false;
}
unittest
{
    alias candidate = f;

    assert(candidate("flak") == false);
}
void main(){}
