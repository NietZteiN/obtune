#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    for (int i = 0; i < array.size(); i++) {
        if (array[i] < 0) {
            array.erase(array.begin() + i);
            i--; // decrement i to stay at the same index after erasing
        }
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>()));
}
