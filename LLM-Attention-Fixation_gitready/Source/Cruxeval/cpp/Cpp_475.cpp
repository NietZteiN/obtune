#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> array, long index) {
    if (index < 0) {
        index = array.size() + index;
    }
    return array[index];
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1})), (0)) == (1));
}
