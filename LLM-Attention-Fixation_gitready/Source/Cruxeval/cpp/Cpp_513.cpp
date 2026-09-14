#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    while(std::find(array.begin(), array.end(), -1) != array.end()) {
        array.erase(array.end() - 3);
    }
    while(std::find(array.begin(), array.end(), 0) != array.end()) {
        array.pop_back();
    }
    while(std::find(array.begin(), array.end(), 1) != array.end()) {
        array.erase(array.begin());
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)2}))) == (std::vector<long>()));
}
