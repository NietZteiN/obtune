#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string x) {
    std::string result;
    for (int i = x.size() - 1; i >= 0; --i) {
        result += x[i];
        if (i != 0) {
            result += " ";
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("lert dna ndqmxohi3")) == ("3 i h o x m q d n   a n d   t r e l"));
}
