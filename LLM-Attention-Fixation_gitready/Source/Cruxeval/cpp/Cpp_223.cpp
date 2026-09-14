#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> array, long target) {
    long count = 0;
    long i = 1;
    for (int j = 1; j < array.size(); j++) {
        if ((array[j] > array[j-1]) && (array[j] <= target)) {
            count += i;
        } else if (array[j] <= array[j-1]) {
            i = 1;
        } else {
            i += 1;
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)-1, (long)4})), (2)) == (1));
}
