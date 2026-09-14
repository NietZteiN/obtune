#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    long prev = array[0];
    std::vector<long> newArray = array;
    for (int i = 1; i < array.size(); i++) {
        if (prev != array[i]) {
            newArray[i] = array[i];
        } else {
            newArray.erase(newArray.begin() + i);
            i--;
        }
        prev = array[i];
    }
    return newArray;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3}))) == (std::vector<long>({(long)1, (long)2, (long)3})));
}
