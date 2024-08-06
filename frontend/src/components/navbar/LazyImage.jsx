import React from 'react';
import LazyLoad from 'react-lazyload';

const LazyImage = ({ src, alt, width, height}) => {
    return <img src={src} alt={alt} loading="lazy" style={{ width: width, height: height }} />;
};

export default LazyImage;
