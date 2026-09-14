import std.math;
import std.typecons;
import std.algorithm;

bool f(string st, string[] pattern) 
{
    foreach(p; pattern) {
        if(!st.startsWith(p)) {
            return false;
        }
        st = st[p.length .. $];
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("qwbnjrxs", ["jr", "b", "r", "qw"]) == false);
}
void main(){}
