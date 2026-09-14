import std.math;
import std.typecons;
import std.algorithm;

long[][] f(long[][] vectors) 
{
    long[][] sorted_vecs = [];
    foreach (vec; vectors) {
        vec.sort();
        sorted_vecs ~= vec;
    }
    return sorted_vecs;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}
