import std.math;
import std.typecons;
import std.uni;

Tuple!(long, long) f(string text) {
    long ws = 0;
    foreach (s; text) {
        if (isWhite(s)) {
            ws += 1;
        }
    }
    return tuple(ws, cast(long)text.length);
}

unittest
{
    alias candidate = f;

    assert(candidate("jcle oq wsnibktxpiozyxmopqkfnrfjds") == tuple(2L, 34L));
}
void main(){}
