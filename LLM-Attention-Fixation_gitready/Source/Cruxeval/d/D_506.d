import std.math;
import std.typecons;
import std.conv;
import std.range;

string f(long n) 
{
    string p = "";
    if (n % 2 == 1) {
        p ~= "sn";
    } else {
        return to!string(n * n);
    }
    foreach(x; iota(1, n + 1)) {
        if (x % 2 == 0) {
            p ~= "to";
        } else {
            p ~= "ts";
        }
    }
    return p;
}
unittest
{
    alias candidate = f;

    assert(candidate(1L) == "snts");
}
void main(){}
