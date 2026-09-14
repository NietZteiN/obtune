import std.math;
import std.typecons;
import std.conv;
import std.algorithm;
import std.array;
import std.string;

string f(string x, string y) {
    char[] yMutable = y.dup;
    yMutable.reverse();
    string tmp = yMutable.map!(c => c == '9' ? '0' : '9').array.map!(c => c.to!string).array.join("");
    if (x.isNumeric && tmp.isNumeric) {
        return x ~ tmp;
    } else {
        return x;
    }
}

unittest
{
    alias candidate = f;

    assert(candidate("", "sdasdnakjsda80") == "");
}
void main(){}
