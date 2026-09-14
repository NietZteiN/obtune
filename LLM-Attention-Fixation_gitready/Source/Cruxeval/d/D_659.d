import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;
import std.ascii;

long f(string[] bots) {
    string[] clean;
    foreach (username; bots) {
        if (!username.all!(c => isUpper(c))) {
            clean ~= username[0..2] ~ username[$-3..$];
        }
    }
    return clean.length;
}

unittest
{
    alias candidate = f;

    assert(candidate(["yR?TAJhIW?n", "o11BgEFDfoe", "KnHdn2vdEd", "wvwruuqfhXbGis"]) == 4L);
}
void main(){}
