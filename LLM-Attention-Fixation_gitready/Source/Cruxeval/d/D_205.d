import std.math;
import std.typecons;

string f(string a) 
{
    foreach (_; 0 .. 10) {
        foreach (j; 0 .. a.length) {
            if (a[j] != '#') {
                a = a[j .. $];
                break;
            }
        }
        if (a.length == 0 || a[$ - 1] != '#') {
            break;
        }
        a = a[0 .. $ - 1];
    }
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate("##fiu##nk#he###wumun##") == "fiu##nk#he###wumun");
}
void main(){}
