import std.algorithm;
import std.array;
import std.string;

string f(string text) {
    int t = 5;
    string[] tab;
    foreach (i; text) {
        if (canFind("aeiouy", i.toLower())) {
            string repeated = "";
            foreach (_; 0 .. t) {
                repeated ~= i.toUpper();
            }
            tab ~= repeated;
        } else {
            string repeated = "";
            foreach (_; 0 .. t) {
                repeated ~= i;
            }
            tab ~= repeated;
        }
    }
    return tab.join(" ");
}

unittest
{
    alias candidate = f;

    assert(candidate("csharp") == "ccccc sssss hhhhh AAAAA rrrrr ppppp");
}
void main(){}
