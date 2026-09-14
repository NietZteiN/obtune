import std.math;
import std.typecons;
import std.conv;

string f(string text) 
{
    int count = countOccurrences(text, text[0]);
    auto ls = text.dup;
    foreach (_; 0 .. count) {
        ls = ls[1 .. $];
    }
    return to!string(ls);
}

int countOccurrences(string text, char c)
{
    int count = 0;
    foreach (char ch; text) {
        if (ch == c) {
            count++;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate(";,,,?") == ",,,?");
}
void main(){}
