import std.algorithm;
import std.array;
import std.string;
import std.conv;
import std.ascii : isUpper, isLower, toLower, toUpper;

string f(string line) {
    int count = 0;
    char[] a;
    foreach (i, c; line) {
        count += 1;
        if (count % 2 == 0) {
            if (isUpper(c)) {
                a ~= toLower(c);
            } else if (isLower(c)) {
                a ~= toUpper(c);
            } else {
                a ~= c;
            }
        } else {
            a ~= c;
        }
    }
    return a.to!string;
}

unittest
{
    alias candidate = f;

    assert(candidate("987yhNSHAshd 93275yrgSgbgSshfbsfB") == "987YhnShAShD 93275yRgsgBgssHfBsFB");
}
void main(){}
