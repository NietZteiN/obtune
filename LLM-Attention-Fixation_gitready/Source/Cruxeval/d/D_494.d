import std.math;
import std.typecons;
string f(string num, long l) 
{
    string t = "";
    while (l > num.length) {
        t ~= '0';
        l--;
    }
    return t ~ num;
}
unittest
{
    alias candidate = f;

    assert(candidate("1", 3L) == "001");
}
void main(){}
