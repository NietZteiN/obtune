import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.conv;

string f(string strs) 
{
    auto strsArr = strs.split();

    for (size_t i = 1; i < strsArr.length; i += 2) {
        strsArr[i] = strsArr[i].dup.reverse.idup;
    }

    return strsArr.join(" ");
}

unittest
{
    alias candidate = f;

    assert(candidate("K zBK") == "K KBz");
}
void main(){}
