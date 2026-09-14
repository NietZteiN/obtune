#include<assert.h>
#include<bits/stdc++.h>
bool f(std::vector<long> lst) {
    lst.clear();
    for (long i : lst) {
        if (i == 3) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)0}))) == (true));
}
