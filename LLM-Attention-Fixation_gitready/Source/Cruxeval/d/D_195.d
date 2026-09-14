import std.algorithm;
import std.string;

string f(string text) {
    foreach (p; ["acs", "asp", "scn"]) {
        if (text.startsWith(p)) {
            text = text[p.length .. $] ~ " ";
        } else {
            text = text ~ " ";
        }
    }
    if (text.startsWith(" ")) {
        text = text[1 .. $];
    }
    return text[0 .. $ - 1];
}

unittest
{
    alias candidate = f;

    assert(candidate("ilfdoirwirmtoibsac") == "ilfdoirwirmtoibsac  ");
}
void main(){}
