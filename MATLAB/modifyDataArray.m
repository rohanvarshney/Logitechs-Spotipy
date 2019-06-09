function [dataArrayModified] = modifyDataArray(dataArray)

[A B] = size(dataArray);
length = A;
lengthOfArray = length/14;

dataArrayModified = reshape(dataArray, [lengthOfArray, 14]);

end

