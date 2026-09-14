import std.algorithm : sort, canFind, remove, count;
import std.array : array;
import std.stdio : writeln;

long f(long[] places, long[] lazyPlaces) {
    places.sort();
    foreach (lazyPlace; lazyPlaces) {
        if (places.canFind(lazyPlace)) {
            places = places.remove!(a => a == lazyPlace).array;
        }
    }
    if (places.length == 1) {
        return 1;
    }
    foreach (i, place; places) {
        if (places.count!(a => a == place + 1) == 0) {
            return i + 1;
        }
    }
    return places.length;
}

unittest
{
    alias candidate = f;

    assert(candidate([375L, 564L, 857L, 90L, 728L, 92L], [728L]) == 1L);
}
void main(){}
