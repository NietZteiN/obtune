import std.math;
import std.typecons;
string f(string st) 
{
    if (st[0] == '~') {
        string e = st;
        while (e.length < 10) {
            e = "s" ~ e;
        }
        return f(e);
    } else {
        while (st.length < 10) {
            st = "n" ~ st;
        }
        return st;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("eqe-;ew22") == "neqe-;ew22");
}
void main(){}
