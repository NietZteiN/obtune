import std.math;
import std.typecons;
import std.array;

string f(string text) 
{
    auto a = text.split('\n');
    string[] b;
    foreach (i; 0 .. a.length) {
        auto c = a[i].replace('\t', "    ");
        b ~= c;
    }
    return b.join("\n");
}
unittest
{
    alias candidate = f;

    assert(candidate("			tab tab tabulates") == "            tab tab tabulates");
}
void main(){}
