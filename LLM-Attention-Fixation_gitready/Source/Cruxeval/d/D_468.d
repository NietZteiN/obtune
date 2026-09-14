import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string a, string b, long n) 
{
    string result = b;
    string m = b;
    foreach (_; 0 .. n) {
        if (m != "") {
            auto index = a.indexOf(m);
            if (index != -1) {
                a = a[0 .. index] ~ a[index + m.length .. $];
                m = "";
                result = m = b;
            }
        }
    }
    return a.split(b).join(result);
}
unittest
{
    alias candidate = f;

    assert(candidate("unrndqafi", "c", 2L) == "unrndqafi");
}
void main(){}
