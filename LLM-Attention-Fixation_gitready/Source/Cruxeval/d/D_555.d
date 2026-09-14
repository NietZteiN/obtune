import std.math;
import std.typecons;
import std.string;

string f(string text, long tabstop) {
    text = text.replace("\n", "_____");
    string spaces = "";
    for (int i = 0; i < tabstop; i++) {
        spaces ~= " ";
    }
    text = text.replace("\t", spaces);
    text = text.replace("_____", "\n");
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("odes	code	well", 2L) == "odes  code  well");
}
void main(){}
